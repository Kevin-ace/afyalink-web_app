from flask import Blueprint, render_template, jsonify, flash
from flask_login import login_required
from models import Facility

facility = Blueprint('facility', __name__)

@facility.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard view"""
    try:
        facilities = Facility.get_mapped_facilities()
        facilities_data = [f.to_dict('basic') for f in facilities]
        return render_template('dashboard.html', facilities=facilities_data)
    except Exception as e:
        flash('Error loading facilities data', 'error')
        return render_template('dashboard.html', facilities=[])

@facility.route('/api/facilities')
@login_required
def get_facilities():
    """API endpoint for facilities data"""
    try:
        facilities = Facility.get_mapped_facilities()
        return jsonify([f.to_dict() for f in facilities])
    except Exception as e:
        return jsonify({'error': 'Error loading facilities data'}), 500
