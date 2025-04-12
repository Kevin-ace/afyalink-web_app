from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_login import LoginManager, login_required, current_user
import logging
from logging.handlers import RotatingFileHandler
import os

from auth import auth
from models import User, Facility
from database import db, init_db
from config import Config
from facility_loader import load_facilities_from_csv

def setup_logging(app):
    """Configure application logging"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/afyalink.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Afyalink startup')

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    
    # Setup login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user from ID"""
        try:
            return db.session.get(User, int(user_id))
        except Exception as e:
            app.logger.error(f"Error loading user: {e}")
            return None

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(appointments)

    # Setup logging
    setup_logging(app)

    # Initialize database
    init_db(app)
    with app.app_context():
        # Load facilities data if needed
        load_facilities_from_csv(app)

    # Register routes
    @app.route('/')
    def index():
        """Landing page"""
        return render_template('index.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard view"""
        try:
            facilities = Facility.query.filter(
                Facility.latitude.isnot(None),
                Facility.longitude.isnot(None)
            ).all()
            
            facilities_data = [{
                'id': f.id,
                'name': f.facility_name,
                'latitude': float(f.latitude),
                'longitude': float(f.longitude),
                'county': f.district,
                'contact': f.hmis,
                'facility_type': f.facility_type
            } for f in facilities]
            
            return render_template('dashboard.html', facilities=facilities_data)
        except Exception as e:
            app.logger.error(f"Error loading dashboard: {e}")
            flash('Error loading facilities data', 'error')
            return render_template('dashboard.html', facilities=[])

    @app.route('/profile')
    @login_required
    def profile():
        """User profile page"""
        return render_template('profile.html', user=current_user)

    @app.route('/api/facilities')
    @login_required
    def get_facilities():
        """API endpoint for facilities data"""
        try:
            facilities = Facility.query.filter(
                Facility.latitude.isnot(None),
                Facility.longitude.isnot(None)
            ).all()
            return jsonify([{
                'id': f.id,
                'name': f.facility_name,
                'facility_type': f.facility_type,
                'latitude': float(f.latitude),
                'longitude': float(f.longitude),
                'address': f'{f.location}, {f.district}',
                'contact': f.hmis,
                'services': f.assigned_service,
                'insurance': f.assigned_insurance,
                'province': f.province,
                'district': f.district,
                'division': f.division,
                'location': f.location,
                'sub_location': f.sub_location,
                'agency': f.agency,
                'updated_at': f.updated_at.isoformat() if f.updated_at else None
            } for f in facilities])
        except Exception as e:
            app.logger.error(f"API Error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/about')
    def about():
        """About page"""
        return render_template('about.html')

    return app


def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(auth)

    # Setup login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user from ID"""
        try:
            return db.session.get(User, int(user_id))
        except Exception as e:
            app.logger.error(f"Error loading user: {e}")
            return None

    # Register routes
    @app.route('/')
    def index():
        """Landing page"""
        return render_template('index.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard view"""
        try:
            facilities = Facility.query.filter(
                Facility.latitude.isnot(None),
                Facility.longitude.isnot(None)
            ).all()
            
            facilities_data = [{
                'id': f.id,
                'name': f.facility_name,
                'latitude': float(f.latitude),
                'longitude': float(f.longitude),
                'county': f.district,
                'contact': f.hmis,
                'facility_type': f.facility_type
            } for f in facilities]
            
            return render_template('dashboard.html', facilities=facilities_data)
        except Exception as e:
            app.logger.error(f"Error loading dashboard: {e}")
            flash('Error loading facilities data', 'error')
            return render_template('dashboard.html', facilities=[])

    @app.route('/profile')
    @login_required
    def profile():
        """User profile page"""
        return render_template('profile.html', user=current_user)

    @app.route('/api/facilities')
    @login_required
    def get_facilities():
        """API endpoint for facilities data"""
        try:
            facilities = Facility.query.filter(
                Facility.latitude.isnot(None),
                Facility.longitude.isnot(None)
            ).all()
            return jsonify([{
                'id': f.id,
                'name': f.facility_name,
                'facility_type': f.facility_type,
                'latitude': float(f.latitude),
                'longitude': float(f.longitude),
                'address': f'{f.location}, {f.district}',
                'contact': f.hmis,
                'services': f.assigned_service,
                'insurance': f.assigned_insurance,
                'province': f.province,
                'district': f.district,
                'division': f.division,
                'location': f.location,
                'sub_location': f.sub_location,
                'agency': f.agency,
                'updated_at': f.updated_at.isoformat() if f.updated_at else None
            } for f in facilities])
        except Exception as e:
            app.logger.error(f"API Error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/about')
    def about():
        """About page"""
        return render_template('about.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """User registration"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            try:
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                
                # Validate input
                if not all([username, email, password, confirm_password]):
                    flash('All fields are required', 'error')
                    return redirect(url_for('signup'))
                
                # Check username format
                if len(username) < 3 or len(username) > 20:
                    flash('Username must be between 3 and 20 characters', 'error')
                    return redirect(url_for('signup'))
                
                # Check email format
                if '@' not in email or '.' not in email:
                    flash('Please enter a valid email address', 'error')
                    return redirect(url_for('signup'))
                
                # Check password strength
                if len(password) < 8:
                    flash('Password must be at least 8 characters long', 'error')
                    return redirect(url_for('signup'))
                
                # Check if username exists
                if User.query.filter_by(username=username).first():
                    flash('Username already exists', 'error')
                    return redirect(url_for('signup'))
                    
                # Check if email exists
                if User.query.filter_by(email=email).first():
                    flash('Email already registered', 'error')
                    return redirect(url_for('signup'))
                    
                if password != confirm_password:
                    flash('Passwords do not match', 'error')
                    return redirect(url_for('signup'))
                
                # Create new user
                user = User(username=username, email=email)
                user.set_password(password)
                
                db.session.add(user)
                db.session.commit()
                
                app.logger.info(f"New user registered: {username}")
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Registration error: {e}")
                flash('An error occurred during registration. Please try again.', 'error')
                return redirect(url_for('signup'))
        
        return render_template('auth.html', mode='signup')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = request.form.get('remember', False)
            
            if not username or not password:
                flash('Username and password are required', 'error')
                return redirect(url_for('login'))
            
            try:
                user = User.query.filter_by(username=username).first()
                if user and user.check_password(password):
                    login_user(user, remember=bool(remember))
                    next_page = request.args.get('next')
                    return redirect(next_page if next_page else url_for('dashboard'))
                flash('Invalid username or password', 'error')
            except Exception as e:
                app.logger.error(f"Login error: {e}")
                flash('Error during login', 'error')
            
        return render_template('auth.html', action='login')

    @app.route('/logout')
    @login_required
    def logout():
        """User logout"""
        logout_user()
        flash('You have been logged out successfully', 'info')
        return redirect(url_for('index'))

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
        
    return app

import os
import datetime

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT, default to 5000 if not set
    app.run(host="0.0.0.0", port=port, debug=True)
