from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Appointment, PatientInfo, Facility
from database import db
from datetime import datetime

appointments = Blueprint('appointments', __name__)

@appointments.route('/book-appointment/<int:facility_id>', methods=['POST'])
@login_required
def book_appointment():
    try:
        facility_id = request.form.get('facility_id')
        appointment_date = datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%dT%H:%M')
        
        # Create patient info
        patient_info = PatientInfo(
            full_name=request.form.get('full_name'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d'),
            gender=request.form.get('gender'),
            phone_number=request.form.get('phone_number'),
            address=request.form.get('address'),
            emergency_contact_name=request.form.get('emergency_contact_name'),
            emergency_contact_phone=request.form.get('emergency_contact_phone'),
            medical_history=request.form.get('medical_history'),
            current_medications=request.form.get('current_medications'),
            allergies=request.form.get('allergies'),
            chief_complaint=request.form.get('chief_complaint')
        )
        db.session.add(patient_info)
        db.session.flush()
        
        # Create appointment
        appointment = Appointment(
            user_id=current_user.id,
            facility_id=facility_id,
            appointment_date=appointment_date,
            patient_info_id=patient_info.id
        )
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Appointment booked successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@appointments.route('/my-appointments')
@login_required
def my_appointments():
    appointments = Appointment.query.filter_by(user_id=current_user.id).all()
    return render_template('appointments/my_appointments.html', appointments=appointments)