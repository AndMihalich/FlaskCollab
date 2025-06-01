from flask import render_template, request, redirect, url_for, current_app, flash
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, login_required, current_user
from random import randint

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.email.data).first() or \
                User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Invalid username or password.', 'error')
            redirect(url_for('auth.login'))
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            role_id=1,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            password=form.password.data,
            )
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()

@auth.route('/auth-admin')
def auth_admin():
    admin = User.query.filter_by(role_id=3).first()
    if current_user.is_anonymous:
        login_user(admin)
    elif current_user!=admin:
        logout_user()
        login_user(admin)
    return redirect(url_for('main.userdb_user', username=admin.username, user=admin))

@auth.route('/auth-random')
def auth_random():
    num_users = User.query.count()
    if not num_users==0:
        random_user = User.query.get(randint(1, num_users))
        if current_user.is_anonymous:
            login_user(random_user)
        elif current_user!=random_user:
            logout_user()
            login_user(random_user)
    else:
        return redirect(url_for('.index'))

    return redirect(url_for('main.userdb_user', username=random_user.username, user=random_user))
