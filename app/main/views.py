from . import blue_main as main
from flask import render_template, request, redirect, url_for, flash
from .forms import SearchForm
from app.models import User, Role
from flask_login import login_required
from ..decorators import *
from .. import db
from .forms import EditProfileForm, EditProfileAdminForm


@main.route('/')
def root():
    return redirect(url_for(".home"))

@main.route('/home')
def home():
    return render_template('home.html', content="Hello!")

@main.route('/UserDB', methods=['GET', 'POST'])
# @login_required 
def userdb():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('.userdb_user', username=form.query.data))
    return render_template('UserDB.html', form=form)

@main.route('/UserDB/<username>', methods=['GET', 'POST'])
# @login_required
def userdb_user(username):
    print('UserDB username:', username)
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('.userdb_user', username=form.query.data))
    user = User.query.filter_by(username=username).first()
    print(user, username)
    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('.userdb'))
    return render_template('UserDB_user.html', user=user, form=form, username=username)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.userdb_user', username=current_user.username))
    form.username.data = current_user.username
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.about_me = form.about_me.data
        current_user.email = form.email.data
        
        if current_user == user:
            user.role = Role.query.filter_by(name='Admin').first()
        else:
            user.role = Role.query.get(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated')
        return redirect(url_for('main.userdb_user', username=user.username))

    form.username.data = current_user.username
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.about_me.data = user.about_me
    form.email.data = user.email
    form.role.data = user.role_id

    return render_template('edit_profile.html', form=form, user=user)

@main.route('/UserDB_search')
def userdb_search():
    q = request.args.get('q', '', type=str)
    users = []
    if q:
        users = User.query.filter(User.username.ilike(f"%{q}%")).limit(7).all()
    return {'users': [
        {'username': u.username, 'email': u.email} for u in users
    ]}
