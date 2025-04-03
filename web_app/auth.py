from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from models import User
from models import db  # Import the database instance

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth.html', mode='signup')  # Set mode to 'signup'

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))  # Redirect to your dashboard or home page
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth.html', mode='login')  # Set mode to 'login'

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))  # Redirect to the login page