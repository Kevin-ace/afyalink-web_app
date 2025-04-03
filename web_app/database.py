from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database and migrations"""
    db.init_app(app)
    migrate.init_app(app, db)

def create_tables(app):
    """Create database tables"""
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")
            raise
            
def reset_db(app):
    """Reset database - use with caution!"""
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            app.logger.info("Database reset successfully")
        except Exception as e:
            app.logger.error(f"Error resetting database: {e}")
            raise