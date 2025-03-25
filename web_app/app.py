from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_facilities.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class HealthFacility(db.Model):
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
        if HealthFacility.query.first() is None:
            # Read CSV file
            df = pd.read_csv('Health_Facilities.csv')
            
            # Insert data into database
            for _, row in df.iterrows():
                facility = HealthFacility(
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
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/facilities')
def get_facilities():
    facilities = HealthFacility.query.all()
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

if __name__ == '__main__':
    load_facilities_from_csv()
    app.run(debug=True)
