"""Authentication routes blueprint."""

import logging
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user, login_user, logout_user
from models import db, User

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both customers and restaurant owners."""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            if not username or not password:
                flash('Please fill in all fields.', 'error')
                return render_template('auth/login.html')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password) and user.is_active:
                login_user(user)
                flash(f'Welcome back, {user.first_name}!', 'success')
                if user.is_customer():
                    return redirect(url_for('customer.dashboard'))
                if user.is_restaurant_owner():
                    return redirect(url_for('restaurant.dashboard'))
            else:
                flash('Invalid username or password.', 'error')
        except Exception as exc:  # noqa: BLE001
            logger.error("Error in login: %s", exc)
            flash('An error occurred during login.', 'error')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    try:
        logout_user()
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in logout: %s", exc)
        flash('An error occurred during logout.', 'error')
    return redirect(url_for('main.index'))


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
@login_required
def reset_password():
    """Change password for any logged-in user (customer or owner)."""
    if request.method == 'POST':
        try:
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            if not old_password or not new_password or not confirm_password:
                flash('Please fill in all fields.', 'error')
                return render_template('auth/reset_password.html')
            if not current_user.check_password(old_password):
                flash('Old password is incorrect.', 'error')
                return render_template('auth/reset_password.html')
            if len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'error')
                return render_template('auth/reset_password.html')
            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return render_template('auth/reset_password.html')
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully. Please log in again.', 'success')
            logout_user()
            return redirect(url_for('auth.login'))
        except Exception as exc:  # noqa: BLE001
            logger.error("Error changing password: %s", exc)
            db.session.rollback()
            flash('An error occurred while changing password.', 'error')
    return render_template('auth/reset_password.html')


