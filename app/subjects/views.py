from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from .forms import JoinSubjectForm, CreateSubjectForm, PostMaterialForm
from .. import db
from ..models import Subject, User, subject_students, SubjectPost, Permission, ChatRoom, Message, chat_members
from . import subjects as subj
import secrets, os
from ..decorators import *
import docx


UPLOAD_FOLDER = 'app/static/uploads'


@subj.route('/')
@login_required
def subject_list():
    subjects = Subject.query.filter((Subject.teacher == current_user) | (Subject.students.contains(current_user))).all()
    return render_template('subj/subject_list.html', subjects=subjects)


@subj.route('/create', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CREATE)
def create_subject():
    form = CreateSubjectForm()
    if form.validate_on_submit():
        code = secrets.token_hex(4)[:6].upper()
        subject = Subject(name=form.name.data, teacher=current_user, code=code)
        db.session.add(subject)
        db.session.commit()
        flash('Subject created!', 'success')
        return redirect(url_for('subj.subject_list'))
    return render_template('subj/create_subject.html', form=form)


@subj.route('/join', methods=['GET', 'POST'])
@login_required
def join_subject():
    form = JoinSubjectForm()
    if form.validate_on_submit():
        subject = Subject.query.filter_by(code=form.code.data.upper()).first()
        if subject:
            if current_user not in subject.students:
                subject.students.append(current_user)
                db.session.commit()
                flash('Joined subject successfully!', 'success')
            else:
                flash('You are already in this subject.', 'info')
        else:
            flash('Invalid subject code.', 'danger')
        return redirect(url_for('subj.subject_list'))
    return render_template('subj/join_subject.html', form=form)


@subj.route('/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if current_user != subject.teacher and current_user not in subject.students:
        flash('Access denied.', 'danger')
        return redirect(url_for('subj.subject_list'))

    form = PostMaterialForm()
    if form.validate_on_submit() and current_user == subject.teacher:
        file = form.file.data
        filename = secrets.token_hex(4) + "_" + file.filename
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        post = SubjectPost(title=form.title.data, filename=filename, subject=subject)
        db.session.add(post)
        db.session.commit()
        flash('Material posted!', 'success')
        return redirect(url_for('subj.subject_detail', subject_id=subject.id))

    posts = subject.posts.order_by(SubjectPost.uploaded_at.desc()).all()
    return render_template('subj/subject_detail.html', subject=subject, posts=posts, form=form)


@subj.route('/<int:subject_id>/posts/<int:post_id>')
@login_required
def view_post(subject_id, post_id):
    subject = Subject.query.get_or_404(subject_id)
    post = SubjectPost.query.get_or_404(post_id)

    file_path = os.path.join(current_app.root_path, 'static', 'uploads', post.filename)
    content = ""
    if post.filename.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    elif post.filename.endswith('.docx'):
        doc = docx.Document(file_path)
        content = "\n".join(p.text for p in doc.paragraphs)

    return render_template('subj/view_post.html', subject=subject, post=post, content=content)


@subj.route('/<int:subject_id>/posts/<int:post_id>/ask', methods=['POST'])
@login_required
def ask_question(subject_id, post_id):
    subject = Subject.query.get_or_404(subject_id)
    post = SubjectPost.query.get_or_404(post_id)

    selected_text = request.form.get("selected_text")
    message_text = request.form.get("message")

    teacher = subject.teacher
    existing_chat = ChatRoom.get_or_create_private_chat(current_user, teacher)

    full_message = f"📚 Question on: \"{selected_text}\"\n\n{message_text}"

    msg = Message(
        room=existing_chat,
        sender=current_user,
        content=full_message,
    )
    db.session.add(msg)
    db.session.commit()

    flash("Question sent to your teacher!", "success")
    return redirect(url_for('subj.view_post', subject_id=subject.id, post_id=post.id))