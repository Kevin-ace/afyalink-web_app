import os

class Config:
    # Database configuration
    DB_USER = os.getenv('DB_USER', 'kevin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'afyalink_db')
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    if not os.getenv('DATABASE_URL'):  # Local development
        SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    else:  # Production
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
        if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')  # Change in production!
