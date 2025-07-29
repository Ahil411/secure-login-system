from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.admin import bp
from app import db
from app.models import User, Role, SecurityLog, LoginAttempt
from app.forms import UserManagementForm
from functools import wraps
from datetime import datetime, timedelta
import os

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        if not current_user.has_role('Admin'):
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.dashboard'))

        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    # Calculate statistics
    total_users = User.query.count()
    admin_users = User.query.join(User.roles).filter(Role.name == 'Admin').count()
    regular_users = total_users - admin_users

    # Recent registrations (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= week_ago).count()

    # Login statistics
    successful_logins_today = LoginAttempt.query.filter(
        LoginAttempt.success == True,
        LoginAttempt.timestamp >= datetime.utcnow() - timedelta(days=1)
    ).count()

    failed_logins_today = LoginAttempt.query.filter(
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= datetime.utcnow() - timedelta(days=1)
    ).count()

    # Locked accounts
    locked_accounts = User.query.filter(
        User.locked_until > datetime.utcnow()
    ).count()

    # Recent security events
    recent_events = SecurityLog.query.order_by(
        SecurityLog.timestamp.desc()
    ).limit(10).all()

    stats = {
        'total_users': total_users,
        'admin_users': admin_users,
        'regular_users': regular_users,
        'new_users_week': new_users_week,
        'successful_logins_today': successful_logins_today,
        'failed_logins_today': failed_logins_today,
        'locked_accounts': locked_accounts,
        'recent_events': recent_events
    }

    return render_template('admin/dashboard.html', title='Admin Dashboard', stats=stats)

@bp.route('/users')
@login_required
@admin_required
def users():
    """Manage all users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)

    return render_template('admin/users.html', title='User Management', users=users)

@bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)

    # Get user's login history
    login_history = LoginAttempt.query.filter_by(user_id=user_id).order_by(
        LoginAttempt.timestamp.desc()).limit(20).all()

    # Get user's security logs
    security_logs = SecurityLog.query.filter_by(user_id=user_id).order_by(
        SecurityLog.timestamp.desc()).limit(20).all()

    return render_template('admin/user_detail.html', 
                         title=f'User: {user.username}',
                         user=user,
                         login_history=login_history,
                         security_logs=security_logs)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details"""
    user = User.query.get_or_404(user_id)
    form = UserManagementForm(obj=user)

    # Populate form with current user data
    if request.method == 'GET':
        form.role.data = user.roles[0].name if user.roles else 'User'
        form.is_active.data = user.is_active

    if form.validate_on_submit():
        # Update user details
        user.username = form.username.data
        user.email = form.email.data
        user.is_active = form.is_active.data

        # Update role
        role_name = form.role.data
        role = Role.query.filter_by(name=role_name).first()
        if role:
            user.roles.clear()
            user.roles.append(role)

        db.session.commit()

        # Log the change
        log_entry = SecurityLog(
            user_id=current_user.id,
            action='USER_MODIFIED',
            details=f'Modified user: {user.username}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log_entry)
        db.session.commit()

        flash(f'User {user.username} has been updated successfully.', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/edit_user.html', title='Edit User', form=form, user=user)

@bp.route('/users/<int:user_id>/lock', methods=['POST'])
@login_required
@admin_required
def lock_user(user_id):
    """Lock a user account"""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot lock your own account.', 'error')
        return redirect(url_for('admin.users'))

    user.lock_account(duration_minutes=60)  # Lock for 1 hour

    # Log the action
    log_entry = SecurityLog(
        user_id=current_user.id,
        action='USER_LOCKED',
        details=f'Locked user: {user.username}',
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(log_entry)
    db.session.commit()

    flash(f'User {user.username} has been locked for 1 hour.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/users/<int:user_id>/unlock', methods=['POST'])
@login_required
@admin_required
def unlock_user(user_id):
    """Unlock a user account"""
    user = User.query.get_or_404(user_id)
    user.unlock_account()

    # Log the action
    log_entry = SecurityLog(
        user_id=current_user.id,
        action='USER_UNLOCKED',
        details=f'Unlocked user: {user.username}',
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(log_entry)
    db.session.commit()

    flash(f'User {user.username} has been unlocked.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))

    username = user.username

    # Delete related records first
    LoginAttempt.query.filter_by(user_id=user_id).delete()
    SecurityLog.query.filter_by(user_id=user_id).delete()

    # Delete user
    db.session.delete(user)
    db.session.commit()

    # Log the action
    log_entry = SecurityLog(
        user_id=current_user.id,
        action='USER_DELETED',
        details=f'Deleted user: {username}',
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(log_entry)
    db.session.commit()

    flash(f'User {username} has been deleted.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/security-logs')
@login_required
@admin_required
def security_logs():
    """View all security logs"""
    page = request.args.get('page', 1, type=int)
    logs = SecurityLog.query.order_by(SecurityLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False)

    return render_template('admin/security_logs.html', title='Security Logs', logs=logs)

@bp.route('/login-attempts')
@login_required
@admin_required
def login_attempts():
    """View all login attempts"""
    page = request.args.get('page', 1, type=int)
    attempts = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False)

    return render_template('admin/login_attempts.html', title='Login Attempts', attempts=attempts)

@bp.route('/system-info')
@login_required
@admin_required
def system_info():
    """Display system information"""
    import platform
    import psutil

    system_info = {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': f"{psutil.virtual_memory().total / 1024**3:.2f} GB",
        'disk_usage': f"{psutil.disk_usage('/').percent}%"
    }

    return render_template('admin/system_info.html', title='System Information', info=system_info)

# API endpoints for admin functions
@bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint for admin statistics"""
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'admin_users': User.query.join(User.roles).filter(Role.name == 'Admin').count(),
        'locked_users': User.query.filter(User.locked_until > datetime.utcnow()).count(),
        'recent_logins': LoginAttempt.query.filter(
            LoginAttempt.success == True,
            LoginAttempt.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count(),
        'failed_logins': LoginAttempt.query.filter(
            LoginAttempt.success == False,
            LoginAttempt.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()
    }

    return jsonify(stats)
