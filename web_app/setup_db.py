from flask import Flask
from config import Config
from database import db, init_db, create_tables
from models import User
from facility_loader import load_facilities_from_csv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    return app

def setup_database():
    """Initialize database with tables and load initial data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            create_tables(app)
            logger.info("Database tables created successfully!")
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', email='admin@afyalink.com')
                admin.set_password('admin123')  # Change this in production!
                db.session.add(admin)
                db.session.commit()
                logger.info("Admin user created successfully!")
            
            # Load facilities data
            if load_facilities_from_csv(app):
                logger.info("Facilities data loaded successfully!")
            else:
                logger.error("Failed to load facilities data!")
                
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            raise

if __name__ == '__main__':
    try:
        setup_database()
        logger.info("Database setup completed successfully!")
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise
