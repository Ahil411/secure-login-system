from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.auth import bp
from app import db
from app.models import User, Role, LoginAttempt, SecurityLog
from app.forms import LoginForm, RegistrationForm, ChangePasswordForm
from datetime import datetime
import requests

def log_security_event(action, details=None, user_id=None):
    """Log security-related events"""
    try:
        log_entry = SecurityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Failed to log security event: {e}")

def log_login_attempt(username, success, user_id=None):
    """Log login attempts for security monitoring"""
    try:
        attempt = LoginAttempt(
            user_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            attempted_username=username,
            success=success
        )
        db.session.add(attempt)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Failed to log login attempt: {e}")

def verify_recaptcha(response):
    """Verify reCAPTCHA response"""
    try:
        secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY')
        if not secret_key:
            return True  # Skip verification if no key configured

        payload = {
            'secret': secret_key,
            'response': response,
            'remoteip': request.remote_addr
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
        result = r.json()
        return result.get('success', False)
    except Exception as e:
        current_app.logger.error(f"reCAPTCHA verification failed: {e}")
        return False

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        # Verify reCAPTCHA
        if not verify_recaptcha(request.form.get('g-recaptcha-response')):
            flash('Please complete the reCAPTCHA verification.', 'error')
            return render_template('auth/login.html', title='Sign In', form=form)

        username = form.username.data
        password = form.password.data

        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user is None:
            log_login_attempt(username, False)
            log_security_event('LOGIN_FAILED', f'Unknown username: {username}')
            flash('Invalid username or password', 'error')
            return render_template('auth/login.html', title='Sign In', form=form)

        # Check if account is locked
        if user.is_locked():
            log_login_attempt(username, False, user.id)
            log_security_event('LOGIN_BLOCKED', 'Account locked', user.id)
            flash('Account is temporarily locked due to multiple failed login attempts. Please try again later.', 'error')
            return render_template('auth/login.html', title='Sign In', form=form)

        # Check password
        if not user.check_password(password):
            user.increment_failed_attempts()
            log_login_attempt(username, False, user.id)
            log_security_event('LOGIN_FAILED', f'Wrong password for user: {username}', user.id)

            remaining_attempts = 5 - user.failed_login_attempts
            if remaining_attempts > 0:
                flash(f'Invalid username or password. {remaining_attempts} attempts remaining.', 'error')
            else:
                flash('Account has been locked due to multiple failed login attempts.', 'error')

            return render_template('auth/login.html', title='Sign In', form=form)

        # Successful login
        user.reset_failed_attempts()
        login_user(user, remember=form.remember_me.data)
        log_login_attempt(username, True, user.id)
        log_security_event('LOGIN_SUCCESS', f'User logged in: {username}', user.id)

        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Store tokens in session (in production, use secure storage)
        from flask import session
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

        flash('Login successful!', 'success')

        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.dashboard')

        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Verify reCAPTCHA
        if not verify_recaptcha(request.form.get('g-recaptcha-response')):
            flash('Please complete the reCAPTCHA verification.', 'error')
            return render_template('auth/register.html', title='Register', form=form)

        # Get or create role
        role_name = form.role.data
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=f'{role_name} role')
            db.session.add(role)
            db.session.flush()  # Flush to get the role ID

        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        log_security_event('USER_REGISTERED', f'New user registered: {user.username}', user.id)
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/logout')
@login_required
def logout():
    log_security_event('LOGOUT', f'User logged out: {current_user.username}', current_user.id)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html', title='Change Password', form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()

        log_security_event('PASSWORD_CHANGED', f'Password changed for user: {current_user.username}', current_user.id)
        flash('Your password has been changed successfully.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/change_password.html', title='Change Password', form=form)

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', title='User Profile', user=current_user)

# API Routes for JWT Authentication
@bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for JWT-based login"""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400

        username = data['username']
        password = data['password']

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user or not user.check_password(password):
            log_login_attempt(username, False, user.id if user else None)
            return jsonify({'error': 'Invalid credentials'}), 401

        if user.is_locked():
            return jsonify({'error': 'Account is locked'}), 423

        # Successful login
        user.reset_failed_attempts()
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        log_login_attempt(username, True, user.id)
        log_security_event('API_LOGIN_SUCCESS', f'API login for user: {username}', user.id)

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'roles': [role.name for role in user.roles]
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"API login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def api_refresh():
    """Refresh JWT access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        new_token = create_access_token(identity=current_user_id)

        return jsonify({
            'access_token': new_token
        }), 200

    except Exception as e:
        current_app.logger.error(f"Token refresh error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/api/protected', methods=['GET'])
@jwt_required()
def api_protected():
    """Protected API endpoint example"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    return jsonify({
        'message': 'Access granted',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [role.name for role in user.roles]
        }
    }), 200
