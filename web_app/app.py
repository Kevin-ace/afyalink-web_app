from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_facilities.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key in production

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class Facility(db.Model):
    __tablename__ = 'health_facilities'
    
    id = db.Column(db.Integer, primary_key=True)
    facility_number = db.Column(db.String(50))
    facility_name = db.Column(db.String(255), nullable=False)
    hmis = db.Column(db.String(50))
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    division = db.Column(db.String(100))
    location = db.Column(db.String(100))
    sub_location = db.Column(db.String(100))
    facility_type = db.Column(db.String(50))
    agency = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    assigned_service = db.Column(db.String(255))
    assigned_insurance = db.Column(db.String(255))

def load_facilities_from_csv():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data already exists
        if Facility.query.first() is None:
            # Read CSV file
            df = pd.read_csv('Health_Facilities.csv')
            
            # Insert data into database
            for _, row in df.iterrows():
                facility = Facility(
                    facility_number=str(row['Facility Number']),
                    facility_name=row['Facility Name'],
                    hmis=str(row['HMIS']),
                    province=row['Province'],
                    district=row['District'],
                    division=row['Division'],
                    location=row['LOCATION'],
                    sub_location=row['Sub Location'],
                    facility_type=str(row['Facility Type']),
                    agency=row['Agency'],
                    latitude=float(row['Latitude']),
                    longitude=float(row['Longitude']),
                    assigned_service=row['Assigned Service'],
                    assigned_insurance=row['Assigned Insurance']
                )
                db.session.add(facility)
            
            db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get facilities from the database and convert to dict
    facilities = [{
        'id': f.id,
        'name': f.facility_name,
        'latitude': float(f.latitude) if f.latitude else None,  
        'longitude': float(f.longitude) if f.longitude else None,  
        'county': f.district,
        'contact': f.hmis,
        'facility_type': f.facility_type
    } for f in Facility.query.all() if f.latitude and f.longitude]  
    return render_template('dashboard.html', facilities=facilities)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/api/facilities')
@login_required
def get_facilities():
    facilities = Facility.query.all()
    return jsonify([{
        'id': f.id,
        'name': f.facility_name,
        'facility_type': f.facility_type,
        'latitude': f.latitude,
        'longitude': f.longitude,
        'address': f'{f.location}, {f.district}',
        'contact': f.hmis,
        'services': f.assigned_service,
        'insurance': f.assigned_insurance
    } for f in facilities])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('signup'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth.html', mode='signup')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth.html', action='login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

import os

if __name__ == '__main__':
    load_facilities_from_csv()
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT, default to 5000 if not set
    app.run(host="0.0.0.0", port=port, debug=True)  # Consider turning off debug in production!

