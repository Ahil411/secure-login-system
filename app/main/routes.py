from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.main import bp
from app import db
from app.models import User, SecurityLog, LoginAttempt
from app.forms import ContactForm
from functools import wraps

def role_required(*roles):
    """Decorator to require specific roles"""
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))

            if not any(current_user.has_role(role) for role in roles):
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('main.dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return wrapper

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get user statistics
    total_users = User.query.count()
    recent_logins = LoginAttempt.query.filter_by(success=True).order_by(
        LoginAttempt.timestamp.desc()).limit(5).all()

    user_stats = {
        'total_users': total_users,
        'recent_logins': recent_logins,
        'user_role': [role.name for role in current_user.roles],
        'last_login': current_user.last_login
    }

    return render_template('main/dashboard.html', title='Dashboard', stats=user_stats)

@bp.route('/profile')
@login_required
def profile():
    total_users = User.query.count()
    recent_logins = LoginAttempt.query.filter_by(success=True).order_by(
        LoginAttempt.timestamp.desc()).limit(5).all()

    user_stats = {
        'total_users': total_users,
        'recent_logins': recent_logins,
        'user_role': [role.name for role in current_user.roles],
        'last_login': current_user.last_login
    }
    return render_template('main/dashboard.html', title='Dashboard', stats=user_stats)

@bp.route('/users')
@login_required
@role_required('Admin', 'User')
def users():
    """View all users - accessible to Admin and User roles"""
    users = User.query.all()
    return render_template('main/users.html', title='Users', users=users)

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # In a real application, you would send an email or save to database
        flash(f'Thank you {form.name.data}! Your message has been sent.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('main/contact.html', title='Contact Us', form=form)

@bp.route('/about')
def about():
    return render_template('main/about.html', title='About')

@bp.route('/features')
def features():
    return render_template('main/features.html', title='Features')

@bp.route('/security-logs')
@login_required
@role_required('Admin')
def security_logs():
    """View security logs - Admin only"""
    page = request.args.get('page', 1, type=int)
    logs = SecurityLog.query.order_by(SecurityLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False)

    return render_template('main/security_logs.html', title='Security Logs', logs=logs)

@bp.route('/login-attempts')
@login_required
@role_required('Admin')
def login_attempts():
    """View login attempts - Admin only"""
    page = request.args.get('page', 1, type=int)
    attempts = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False)

    return render_template('main/login_attempts.html', title='Login Attempts', attempts=attempts)

@bp.route('/user-management')
@login_required
@role_required('Admin')
def user_management():
    """User management page - Admin only"""
    users = User.query.all()
    return render_template('main/user_management.html', title='User Management', users=users)

# Error handlers
@bp.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@bp.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500