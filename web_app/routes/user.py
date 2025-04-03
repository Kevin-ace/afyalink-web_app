from flask import Blueprint, render_template
from flask_login import login_required, current_user

user = Blueprint('user', __name__)

@user.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)
