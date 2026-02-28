from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import bp
from app.models import User
from app.forms import LoginForm, RegistrationForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, is_deleted=False).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=(form.remember_me.data == 'yes'))
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if user.is_admin():
                    next_page = url_for('admin.dashboard')
                else:
                    next_page = url_for('main.dashboard')
            return redirect(next_page)
        flash('Invalid username or password', 'error')
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            phone=form.phone.data,
            role='customer'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception as e:
            # Log full traceback and rollback to avoid 500
            current_app.logger.exception('Failed to create new user during registration')
            db.session.rollback()
            flash('An internal error occurred while creating your account. Please try again or contact the administrator.', 'error')
            return render_template('auth/register.html', form=form)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

