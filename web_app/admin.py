@admin.route('/admin/appointments')
@login_required
@admin_required
def manage_appointments():
    appointments = Appointment.query.all()
    return render_template('admin/appointments.html', appointments=appointments)

@admin.route('/admin/appointments/<int:appointment_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_appointment_status():
    appointment = Appointment.query.get_or_404(appointment_id)
    status = request.form.get('status')
    new_date = request.form.get('new_date')
    
    if status not in ['approved', 'declined', 'rescheduled']:
        return jsonify({'status': 'error', 'message': 'Invalid status'}), 400
        
    appointment.status = status
    if status == 'rescheduled' and new_date:
        appointment.appointment_date = datetime.strptime(new_date, '%Y-%m-%dT%H:%M')
    
    db.session.commit()
    return jsonify({'status': 'success'})

@admin.route('/admin/appointments/report')
@login_required
@admin_required
def appointment_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    
    query = Appointment.query
    
    if start_date:
        query = query.filter(Appointment.appointment_date >= start_date)
    if end_date:
        query = query.filter(Appointment.appointment_date <= end_date)
    if status:
        query = query.filter(Appointment.status == status)
        
    appointments = query.all()
    return render_template('admin/appointment_report.html', appointments=appointments)