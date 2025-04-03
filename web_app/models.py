from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Facility(db.Model):
    __tablename__ = 'health_facilities'
    
    id = db.Column(db.Integer, primary_key=True)
    facility_number = db.Column(db.String(50), index=True)  
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
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Facility {self.facility_name}>'
        
    def to_dict(self, format='full'):
        """Convert facility to dictionary for JSON serialization
        
        Args:
            format (str): 'full' for all fields, 'basic' for dashboard view
        """
        if format == 'basic':
            return {
                'id': self.id,
                'name': self.facility_name,
                'latitude': float(self.latitude) if self.latitude else None,
                'longitude': float(self.longitude) if self.longitude else None,
                'county': self.district,
                'contact': self.hmis,
                'facility_type': self.facility_type
            }
        
        return {
            'id': self.id,
            'name': self.facility_name,
            'facility_type': self.facility_type,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'address': f'{self.location}, {self.district}',
            'contact': self.hmis,
            'services': self.assigned_service,
            'insurance': self.assigned_insurance,
            'province': self.province,
            'district': self.district,
            'division': self.division,
            'location': self.location,
            'sub_location': self.sub_location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_mapped_facilities(cls):
        """Get facilities with valid coordinates"""
        return cls.query.filter(
            cls.latitude.isnot(None),
            cls.longitude.isnot(None)
        ).all()