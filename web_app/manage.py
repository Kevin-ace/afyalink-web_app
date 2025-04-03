from flask.cli import FlaskGroup
from app import create_app
from database import db
from models import User, Facility

app = create_app()
cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    """Creates the database tables."""
    db.create_all()
    print("Created database tables.")

@cli.command("drop_db")
def drop_db():
    """Drops the database tables."""
    if input("Are you sure you want to drop all tables? (y/N): ").lower() == 'y':
        db.drop_all()
        print("Dropped all tables.")
    else:
        print("Operation cancelled.")

@cli.command("seed_db")
def seed_db():
    """Seeds the database with initial data."""
    # Create a test admin user
    admin = User(
        username="admin",
        email="admin@afyalink.com"
    )
    admin.set_password("admin123")  # Change this in production!
    db.session.add(admin)
    
    try:
        db.session.commit()
        print("Database seeded with initial data.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {e}")

@cli.command("load_facilities")
def load_facilities():
    """Load facilities from CSV file."""
    try:
        with app.app_context():
            from app import load_facilities_from_csv
            if load_facilities_from_csv(app):
                print("Facilities loaded successfully.")
            else:
                print("Failed to load facilities.")
    except Exception as e:
        print(f"Error loading facilities: {e}")

if __name__ == "__main__":
    cli()
