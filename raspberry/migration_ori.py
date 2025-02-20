from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, SiteData, DeviceInfo, User, SCCData, BMSData, Tenant
import bcrypt
import json
from config import DB_CONFIG

def init_db():
    """Initialize database and create all tables"""
    db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    engine = create_engine(db_url)
    Base.metadata.drop_all(engine)  # Drop existing tables
    Base.metadata.create_all(engine)  # Create new tables
    return engine

def create_initial_data(engine):
    """Create initial static data for database"""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        
        password = '1234'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        admin = User(
            username='admin',
            password=hashed.decode('utf-8'),
            level='admin'
        )
        session.add(admin)
        print("Admin user created successfully")
        
        session.commit()
        print("Initial data creation completed successfully")
        
    except Exception as e:
        session.rollback()
        print(f"Error occurred while creating initial data: {e}")
        raise
    finally:
        session.close()

def main():
    """Main function to run migration"""
    try:
        print("Starting database migration...")
        engine = init_db()
        print("Database tables created successfully")
        
        print("Creating initial data...")
        create_initial_data(engine)
        print("Migration completed successfully")
        
    except Exception as e:
        print(f"Error occurred during migration: {e}")
        raise

if __name__ == '__main__':
    main()